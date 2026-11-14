ParticleDef()
{
	LifeTime()
	{
		keyf(0, 1.5)
	}

	GravityMul()
	{
		randf(0, 1.3, 1.3)
	}

	Drag()
	{
		randf(0, 0.4, 0.4)
	}

	Color()
	{
		keyv4(0, 0.55, 0.55, 0.55, 1)
		keyv4(0.17, 0.55, 0.55, 0.55, 0.86)
		keyv4(0.272, 0.55, 0.55, 0.55, 0.5)
		keyv4(0.9, 0.55, 0.55, 0.55, 0.12)
		keyv4(1.5, 0.55, 0.55, 0.55, 0)
	}

	Size()
	{
		randf(0, 9, 15)
	}

	Rotation()
	{
		randf(0, 0, 360)
	}

	Material("IRN_BloodDrop_particleBLEND.mat", "IRN_BloodDrop_particleBLEND.mat")

	TexMultiRect(2, 2, 4)
	TexPlayMode("random_once", 1)
}
