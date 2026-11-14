ParticleDef()
{
	LifeTime()
	{
		keyf(0, 0.45)
	}

	GravityMul()
	{
		randf(0, 0.05, 0.05)
	}

	Drag()
	{
		randf(0, 3, 3)
	}

	Color()
	{
		keyv4(0, 0.45, 0.45, 0.45, 0.35)
		keyv4(0.45, 0.45, 0.45, 0.45, 0)
	}

	Size()
	{
		keyf(0, 18)
		keyf(0.45, 45)
	}

	Rotation()
	{
		randf(0, 0, 360)
	}

	Material("IRN_BloodMist_particleBLEND.mat", "IRN_BloodMist_particleBLEND.mat")

	TexMultiRect(2, 2, 4)
	TexPlayMode("random_once", 1)
}
