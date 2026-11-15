ParticleDef()
{
	LifeTime()
	{
		keyf(0, 0.5)
	}

	GravityMul()
	{
		randf(0, 0, 0)
	}

	Drag()
	{
		randf(0, 6, 10)
	}

	Color()
	{
		keyv4(0, 0.45, 0.45, 0.45, 0.25)
		keyv4(0.03, 0.45, 0.45, 0.45, 0.45)
		keyv4(0.25, 0.45, 0.45, 0.45, 0.3)
		keyv4(0.5, 0.45, 0.45, 0.45, 0)
	}

	Size()
	{
		randf(0, 36, 50)
	}

	Rotation()
	{
		randf(0, 0, 360)
	}

	Material("IRN_BloodMist_particleBLEND.mat", "IRN_BloodMist_particleBLEND.mat")

	TexMultiRect(2, 2, 4)
	TexPlayMode("random_once", 1)
}
