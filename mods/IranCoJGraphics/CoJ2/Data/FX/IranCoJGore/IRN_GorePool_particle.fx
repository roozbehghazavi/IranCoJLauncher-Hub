ParticleDef()
{
	LifeTime()
	{
		keyf(0, 1)
	}

	GravityMul()
	{
		randf(0, 1.5, 1.5)
	}

	Drag()
	{
		randf(0, 0.5, 0.5)
	}

	Color()
	{
		keyv4(0, 1, 1, 1, 0)
		keyv4(1, 1, 1, 1, 0)
	}

	Size()
	{
		keyf(0, 4)
	}

	Rotation()
	{
		randf(0, 0, 360)
	}

	Material("IRN_BloodDrop_particleBLEND.mat", "IRN_BloodDrop_particleBLEND.mat")

	TexMultiRect(2, 2, 4)
	TexPlayMode("random_once", 1)
}
